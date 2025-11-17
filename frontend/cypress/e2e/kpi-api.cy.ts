describe('KPI API smoke test', () => {
  const authHeader = () => `Bearer ${Cypress.env('bypassToken')}`;

  it('returns executive KPIs', () => {
    cy.request({
      method: 'GET',
      url: '/api/kpis?category=executive',
      headers: {
        Authorization: authHeader(),
      },
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.length.greaterThan(0);
      expect(response.body[0]).to.have.property('name');
    });
  });
});
